import maya.cmds as cmds
import maya.mel as mel
import shutil
import os


def copy_all_textures_to_target(target_directory, include_udims=False):
    """
    增强版：拷贝所有类型的纹理到指定目录

    Args:
        target_directory (str): 目标目录路径
        include_udims (bool): 是否包含UDIM纹理
    """

    # 检查目标目录
    if not os.path.exists(target_directory):
        try:
            os.makedirs(target_directory)
            print("创建目标目录: " + target_directory)
        except Exception as e:
            cmds.error("无法创建目标目录: " + str(e))
            return

    # 获取各种类型的纹理节点
    file_nodes = cmds.ls(type='file')
    image_plane_nodes = cmds.ls(type='imagePlane')

    all_texture_paths = []

    # 处理文件纹理节点
    for file_node in file_nodes:
        try:
            texture_path = cmds.getAttr(file_node + '.fileTextureName')
            if texture_path:
                all_texture_paths.append(texture_path)
        except:
            pass

    # 处理图像平面
    for img_plane in image_plane_nodes:
        try:
            texture_path = cmds.getAttr(img_plane + '.imageName')
            if texture_path:
                all_texture_paths.append(texture_path)
        except:
            pass

    # 去重
    unique_paths = list(set(all_texture_paths))

    copied_files = []
    skipped_files = []
    error_files = []

    for texture_path in unique_paths:
        if not texture_path:
            continue

        try:
            filename = os.path.basename(texture_path)

            # 处理UDIM纹理
            if include_udims and '<UDIM>' in texture_path:
                # 获取UDIM纹理的所有文件
                udim_files = find_udim_files(texture_path)
                for udim_file in udim_files:
                    udim_filename = os.path.basename(udim_file)
                    target_path = os.path.join(target_directory, udim_filename)

                    if os.path.exists(udim_file) and not os.path.exists(target_path):
                        shutil.copy2(udim_file, target_path)
                        copied_files.append(udim_filename)
            else:
                # 普通纹理文件
                target_path = os.path.join(target_directory, filename)

                if os.path.exists(texture_path):
                    if not os.path.exists(target_path):
                        shutil.copy2(texture_path, target_path)
                        copied_files.append(filename)
                        print("已拷贝: " + filename)
                    else:
                        skipped_files.append(filename)
                        print("已存在，跳过: " + filename)
                else:
                    error_files.append(texture_path)
                    print("源文件不存在: " + texture_path)

        except Exception as e:
            error_files.append(texture_path)
            print("处理文件时出错 {}: {}".format(texture_path, str(e)))

    # 显示结果
    print("\n=== 贴图拷贝完成 ===")
    print("目标目录: " + target_directory)
    print("成功拷贝: {} 个文件".format(len(copied_files)))
    print("跳过文件: {} 个".format(len(skipped_files)))
    print("错误文件: {} 个".format(len(error_files)))

    return copied_files


def find_udim_files(udim_pattern):
    """
    查找UDIM纹理的所有文件
    """
    import glob

    # 将<UDIM>替换为通配符
    search_pattern = udim_pattern.replace('<UDIM>', '*')
    directory = os.path.dirname(udim_pattern)

    if not directory:
        directory = os.path.dirname(cmds.file(q=True, sceneName=True)) or ''

    full_pattern = os.path.join(directory, os.path.basename(search_pattern))
    return glob.glob(full_pattern)


# 运行函数
if __name__ == "__main__":
    # 使用UI选择目录
    target_dir = cmds.fileDialog2(dialogStyle=2, fileMode=3, caption="选择贴图保存目录")
    if target_dir:
        copy_all_textures_to_target(target_dir[0])