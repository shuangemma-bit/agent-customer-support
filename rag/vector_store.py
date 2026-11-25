import os.path
from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import txt_loader, pdf_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.path_tool import get_abs_path
import os
from utils.logger_handler import logger
from langchain_core.documents import Document


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )

        #分割器用递归文本分割器
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,  #如何计算文本长度
        )

    #创建并返回检索器
    def get_retrieve(self):
        return self.vector_store.as_retriever(search_kwargs = {"k": chroma_conf["k"]})


    def load_document(self):
        """
        从数据文件夹内读取数据文件，并向量存入向量库
        要计算md5去重？
        :return:None
        """

        def check_md5_hex(md5_for_check: str):
            #定义一个函数，用来检查MD5是否已经被记录
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):

                #如果不存在就创建一个空文件
                open(get_abs_path(chroma_conf["md5_hex_store"]),"w",encoding="utf-8").close()
                return False

            #如果存在就遍历内容找到了就返回存在，否则就是不存在
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:

                # 读取文件中所有行，返回一个列表
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True

                return False

        #接收需要保存的 MD5 字符串
        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check+"\n")

        #接收需要读取的文件路径
        def get_file_documents(read_path:str):

            #TXT文件，就调用 TXT 文件加载器，返回加载结果
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            #两种条件都不满足，说明当前函数不支持该文件类型，返回空列表
            return []

        #获取知识库文件夹中所有符合要求的文件路径
        allowed_file_path: list[str] = listdir_with_allowed_type(
            chroma_conf["data_path"], #知识库文件夹路径
            tuple(chroma_conf["allow_knowledge_file_type"]), #允许的文件类型，转换为元组
        )

        #遍历符合要求的文件路径
        for path in allowed_file_path:

            #读取当前文件内容，计算文件的md5
            md5_hex = get_file_md5_hex(path)

            #检查是否在MD5记录中
            #如果返回True，说明文件处理过
            if check_md5_hex(md5_hex):

                #记录日志，说明该文件在知识库中
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")

                continue

            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                #使用文本分割器，将长文本分割成多个小文本块
                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue

                #将内容存到向量库
                self.vector_store.aadd_documents(split_document)

                #记录这个处理好的md5文件，避免下次重复处理
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path}加载内容成功")

            except Exception as e:

                #会记录详细的报错堆栈，反则是错误本身
                logger.error(f"[加载知识库]{path}加载内容失败{str(e)}", exc_info=True)



if __name__ == '__main__':

    vs = VectorStoreService()

    vs.load_document()

    retriever = vs.get_retriever()

    res = retriever.invoke("迷路")

    for r in res:

        print(r.page_content)

        print("-" * 20)