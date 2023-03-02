# 导入所需的包
import pydicom
from pynetdicom import AE, evt, AllStoragePresentationContexts
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove
from tqdm import trange

"""
    用cnt来记录总共存储了多少个数据,可以在jupyter里面输出cnt
"""
cnt = 0
""" 这里设置目标pacs和端口"""



# 定义一个处理函数，用于接收和保存 DICOM 文件
def store_in_localhost(event):
    cnt+=1
    """Handle a C-STORE request event."""
    ds = event.dataset
    ds.file_meta = event.file_meta

    # 保存 DICOM 文件到本地，文件名为 SOPInstanceUID.dcm
    ds.save_as(ds.SOPInstanceUID, write_like_original=False)

    # 返回一个成功的状态码
    return 0x0000

"""
    这里要读取一个文件并获取它的SOP类型
"""
targetAEPort = 15112
targetAE = AE()
targetAE.ae_title = b'DCM4CHEE'
targetAE.supported_contexts = AllStoragePresentationContexts
targetAE.add_requested_context()
targetAssoc = targetAE.associate('192.168.7.197', 11112, ae_title=b'DCM4CHEE')


def send_to_pacs(event):
    """send the dcm file to target pacs server directly"""
    ds = event.dataset
    ds.file_meta = event.file_meta

    # 传送 dcm 文件到pacs，为了保证效率，不每次都新建连接。
    if targetAssoc.is_established:
        status = targetAssoc.send_c_store(ds)
        if status  not in [0x0117,0x0122,0x0124,0x0210,0x0211,0x0212]:
            cnt+=1
        else: 
            errorCnt+=1




# 创建一个应用实体，并设置端口号
ae = AE()
ae.ae_title = b'DCM4CHEE'
ae.network_timeout = None
ae.acse_timeout = None
ae.dimse_timeout = None
ae.maximum_associations = 10

# 添加需要查询和获取的 DICOM 文件的类型, 读一个文件获取它的类型
"""
    这里要读取一个文件并获取它的SOP类型
"""
ae.add_requested_context()
ae.supported_contexts = AllStoragePresentationContexts

# 绑定处理函数到事件上，以便在收到 DICOM 文件时执行该函数
"""或者不存本地, 使用sendToPacs直接传进pacs"""
handlers = [(evt.EVT_C_STORE, store_in_localhost)]

# 启动一个监听服务，等待 PACS 服务器发送 DICOM 文件过来
"""
    这里设置端口
"""
port = 10247
ae.start_server(('127.0.0.1', port), block=False, evt_handlers=handlers)

# 连接到 PACS 服务器，IP 地址为 '127.0.0.1'，端口号为 104，应用实体标题为 'DCM4CHEE'
assoc = ae.associate('192.168.7.178', 11112, ae_title=b'DCM4CHEE')

if assoc.is_established:
    # 使用 PatientID 来指定查询条件，这里以 '12345678' 为例
    # 您可以根据需要添加或修改查询条件
    responses = assoc.send_c_find('', PatientRootQueryRetrieveInformationModelMove)

    for (status, identifier) in trange(responses):
        if status:
            print('C-FIND query status: 0x{0:04x}'.format(status.Status))

            # 如果查询结果不为空，则发送 C-MOVE 消息给 PACS 服务器，并指定目标应用实体标题为 'DCM4CHEE'
            if status.Status in (0xFF00, 0xFF01):
                assoc.send_c_move(identifier, b'DCM4CHEE', PatientRootQueryRetrieveInformationModelMove)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # 断开与 PACS 服务器的连接
    assoc.release()
else:
    print('Association rejected, aborted or never connected')