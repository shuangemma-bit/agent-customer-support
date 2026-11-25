#md5用来去重复内容
import os.path
from utils.logger_handler import logger
import hashlib
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


#把文件给我，md5去重判断
def get_file_md5_hex(filepath: str):

    #路径不存在
    if not os.path.exists(filepath):
        logger.error(f"md5计算文件{filepath}不存在")
        return

    #不是文件，可能是文件夹
    if not os.path.isfile(filepath):
        logger.error(f"md5计算文件{filepath}不是文件")
        return

    #创建一个 MD5 对象，用于接收文件内容并计算哈希值。
    md5_obj = hashlib.md5()

    #可不写死，避免一次性读取整个大文件，占用过多内存
    chunk_size = 4096

    #b-binary二进制，md5需要接收字节数据，所以用rb
    try:
        with open(filepath,"rb") as f:
            chunk = f.read(chunk_size)
            while chunk:
                md5_obj.update(chunk)
                chunk = f.read(chunk_size)

            #将计算结果转换成一个由 32 个十六进制字符组成的字符串。
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None

#返回文件夹内的文件列表（允许的文件后缀）tuple不可修改
def listdir_with_allowed_type(path: str, allowed_type: tuple[str]):
    files= []

    if not os.path.isdir(path):
        logger.error(f"listdir_with_allowed_type{path}不是文件夹")
        return allowed_type

    for f in os.listdir(path):
        if f.endswith(allowed_type):
            files.append(os.path.join(path,f))

    #返回的内容不希望被修改，将列表转换成元组并返回。
    return tuple(files)


def pdf_loader(filepath:str, passwd=None)->list[Document]:
    return PyPDFLoader(filepath,passwd).load()


def txt_loader(filepath:str)->list[Document]:
    return TextLoader(filepath).load()