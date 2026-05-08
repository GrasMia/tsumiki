from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, func, select, insert, update

from app.models import File, Dir
from app.exceptions import DIR_ALREADY_EXISTS

from .file_service import FileService


class DirService:

    @staticmethod
    async def create_dir(current_dir: Dir, dir_name: str, db: AsyncSession):
        existing_dir = await db.scalar(select(Dir).where(Dir.path == (current_dir.path + dir_name + "/")))
        if existing_dir:
            raise DIR_ALREADY_EXISTS

        await db.execute(
            insert(Dir).values(
                name=dir_name,
                path=current_dir.path + dir_name + "/",
                user_id=current_dir.user_id,
                parent_id=current_dir.id,
            )
        )

        await db.commit()

    @staticmethod
    async def delete_dir(delete_dir: Dir, db: AsyncSession):
        # 递归获取所有子目录ID
        dirs_id = await DirService._get_all_subdir_id(delete_dir.id, db)
        dirs_id.append(delete_dir.id)

        # 获取这些目录下的所有文件
        result = await db.scalars(select(File).where(File.dir_id.in_(dirs_id)).with_for_update())
        files_to_delete = result.all()

        # 删除所有文件
        physical_paths = await FileService.delete_files(files_to_delete, delete_dir.user_id, db=db)

        # 删除所有目录
        await db.execute(delete(Dir).where(Dir.id.in_(dirs_id)))

        await db.commit()

        for physical_path in physical_paths:
            if physical_path.exists():
                physical_path.unlink()

        return [File.name for File in files_to_delete]

    @staticmethod
    async def rename_dir(rename_dir: Dir, new_name: str, db: AsyncSession):
        old_path = rename_dir.path
        parent_path = f"/{"/".join(old_path.strip("/").split("/")[:-1])}/"
        new_path = f"{parent_path}{new_name}/"

        # 检查目标路径
        existing_dir = await db.scalar(select(Dir).where(Dir.path == new_path))
        if existing_dir:
            raise DIR_ALREADY_EXISTS

        # 获取所有子目录ID
        dirs_id = await DirService._get_all_subdir_id(rename_dir.id, db)
        dirs_id.append(rename_dir.id)

        # 批量更新路径
        for dir_id in dirs_id:
            # 使用正则 regexp_replace 而不是 replace 替换路径中的旧路径为新路径
            # 注意：regexp_replace 默认只替换第一个匹配项，不会像 replace 那样替换全部
            # 例如：/3/aaa/m/3/aaa/ 中的 /3/aaa/ 只会替换开头的那个，后面那个不会匹配
            # 要替换所有匹配项需要加全局标志 'g'，如：func.regexp_replace(Dir.path, old_path, new_path, 'g')
            # ^ 锚点的作用是"匹配项必须以对应字符串开头" → f"^{old_path}" 也只会匹配开头的那个 /3/aaa/（即使加上 'g' 标志）
            stmt = update(Dir).where(Dir.id == dir_id).values(path=func.regexp_replace(Dir.path, old_path, new_path))
            await db.execute(stmt)

        rename_dir.name = new_name

        await db.commit()

    @staticmethod
    async def _get_all_subdir_id(delete_dir_id: int, db: AsyncSession) -> list[int]:
        subdirs_id: list[int] = []
        queue = [delete_dir_id]

        while queue:
            current_id = queue.pop()

            # 查询 并 锁定(写锁/排他锁) 所有子目录
            result = await db.scalars(select(Dir.id).where(Dir.parent_id == current_id).with_for_update())
            children_id = [row for row in result.fetchall()]

            subdirs_id.extend(children_id)
            queue.extend(children_id)

        return subdirs_id
