"""
文件上传与文本提取服务。
"""
from pathlib import Path
from typing import Optional, Tuple
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.utils.text_extractor import extract_text


class FileValidationError(HTTPException):
    """文件校验异常。"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _validate_and_read(upload_file: UploadFile) -> tuple[str, bytes]:
    original_name = upload_file.filename or ""
    suffix = Path(original_name).suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise FileValidationError("不支持的文件类型")

    contents = upload_file.file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise FileValidationError("文件过大，请拆分后上传")
    return original_name, contents


def _validate_image_and_read(upload_file: UploadFile) -> tuple[str, bytes]:
    original_name = upload_file.filename or ""
    suffix = Path(original_name).suffix.lower()
    if suffix not in settings.IMAGE_ALLOWED_EXTENSIONS:
        raise FileValidationError("不支持的图片格式")

    contents = upload_file.file.read()
    if not contents:
        raise FileValidationError("图片内容为空")
    if len(contents) > settings.MAX_IMAGE_SIZE:
        raise FileValidationError("图片过大，请压缩后重试")
    return original_name, contents


def save_upload_file(upload_file: UploadFile) -> Path:
    """
    校验上传文件并保存到本地，返回保存后的路径。
    """
    original_name, contents = _validate_and_read(upload_file)

    _ensure_directory(Path(settings.UPLOAD_DIR))
    file_id = uuid4().hex
    suffix = Path(original_name).suffix.lower()
    target_path = Path(settings.UPLOAD_DIR) / f"{file_id}{suffix}"

    with target_path.open("wb") as f:
        f.write(contents)

    upload_file.file.close()
    return target_path


def store_upload_file(upload_file: UploadFile) -> tuple[Path, str]:
    """
    保存上传文件并返回路径与原始文件名。
    """
    original_name, contents = _validate_and_read(upload_file)

    _ensure_directory(Path(settings.UPLOAD_DIR))
    file_id = uuid4().hex
    suffix = Path(original_name).suffix.lower()
    target_path = Path(settings.UPLOAD_DIR) / f"{file_id}{suffix}"

    with target_path.open("wb") as f:
        f.write(contents)

    upload_file.file.close()
    return target_path, original_name


def store_and_extract(upload_file: UploadFile) -> Tuple[Path, str]:
    """
    保存上传文件并返回提取的纯文本。
    """
    saved_path, _ = store_upload_file(upload_file)
    try:
        text = extract_text(saved_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"文件解析失败：{exc}",
        ) from exc
    return saved_path, text


def _static_relative_path(target_path: Path) -> str:
    try:
        relative = target_path.relative_to(Path("static"))
    except ValueError:
        # 若目录配置发生改变，退化为返回绝对路径
        return target_path.as_posix()
    return relative.as_posix()


def remove_static_file(public_path: Optional[str]) -> None:
    """
    删除静态目录下的文件。
    """
    if not public_path:
        return
    relative = public_path
    if relative.startswith("/static/"):
        relative = relative[len("/static/") :]
    relative = relative.lstrip("/")
    if not relative:
        return
    target_path = Path("static") / Path(relative)
    try:
        if target_path.is_file():
            target_path.unlink()
    except OSError:
        # 忽略删除失败，避免影响主流程
        pass


def store_question_image(
    upload_file: UploadFile, *, old_path: Optional[str] = None
) -> tuple[str, str]:
    """
    保存题目图片并返回相对路径与可公开访问的路径。
    """
    original_name, contents = _validate_image_and_read(upload_file)

    image_dir = Path(settings.IMAGE_DIR)
    _ensure_directory(image_dir)

    suffix = Path(original_name).suffix.lower()
    if not suffix:
        suffix = ".png"
    target_path = image_dir / f"{uuid4().hex}{suffix}"

    with target_path.open("wb") as f:
        f.write(contents)

    upload_file.file.close()

    relative_path = _static_relative_path(target_path)
    public_path = (
        relative_path
        if relative_path.startswith("static/")
        else f"/static/{relative_path}"
    )

    # 清理旧图片
    if old_path:
        remove_static_file(old_path)

    # 确保返回前缀以 /static 开头，便于前端拼接
    if not public_path.startswith("/static/"):
        public_path = f"/static/{relative_path.lstrip('/')}"

    return relative_path, public_path
