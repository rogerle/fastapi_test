#--coding:utf-8--**
import json
import re
from typing import Union,Set,List
from fastapi import FastAPI,Request,Body,Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3005",
    "http://localhost?3005"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#登录系统使用
class Item(BaseModel):
    username: str =''
    userPwd: str =''

@app.post("/user/login")
async def user_login(values: Item):
    userTables = {'admin':'123456','test':'000000'}
    userInfo = {'admin':{'Name':'Roger','Gender':'male'},
                'test':{'Name':'TestUser','Gender':'Any'}}
    flag = -1
    userData = {}
    try:
        passwd = userTables[values.username]
        if passwd == values.userPwd:
            flag = 0
            userData = userInfo[values.username]
    except BaseException:
        flag = -1
    return {"message": "Login",'code': flag,'userData': userData}

#定义数字人主播的数据结构
class LiveStreamer(BaseModel):
    id: int = 100001
    name: str = "小七"
    picPath: str = "picpath..."
    defautlVideoPath: str = "defaultVideo..."
    authType: str = "personal"
    audioPath: str = "audioPath..."
    resourcePath: str = "resourcePath..."

#定义播报的切片节目的数据结构
class StreamSlice(BaseModel):
    id: int = 200001
    name: str = "节目切片1"
    voiceText: str = "你好，我是主播，这是第一个产品"
    streamer: Union[LiveStreamer,None] = None
    status: str = "synthesis"

#切片查询获取
@app.get('/slice/{slice_name}')
def get_slices(slice_name: str):
    with open('slices.json','r') as sf:
        slicef = sf.read()
        if len(slicef)>0:
            slice_datas = json.loads(slicef)
        else:
            slice_datas = {"slices":[]}
    #查出想要找的片段
    query_data =[]
    if slice_name is not None:
        for index,slice in enumerate(slice_datas):
            r1 = re.match(slice_name,slice['name'])
            if r1:
                query_data = slice

    return{"message":"query slices","data":query_data}

#创建切片片段数据
@app.post('/slice/create')
def create_slice(slice:StreamSlice):

    with open('id_slices.txt','r') as idf:
        ids = idf.read()
        if len(ids) >0:
            key_id = int(ids)
        else:
            key_id = 0
    slice_id = key_id+1

    #开始创建内容
    streamer = jsonable_encoder(slice.streamer)
    print(streamer)
    slice_data = {"id":slice_id}
    slice_data.update({"name":slice.name,
                       "voiceText":slice.voiceText,
                       "streamer":streamer,
                       "status":slice.status})
    print(slice_data)
    try:
        with open('slices.json','r') as sf:
            sfile = sf.read()
            if len(sfile) > 0:
                slice_datas = json.loads(sfile)
            else:
                slice_datas = {"slice_datas":[]}
        slice_datas['slice_datas'].append(slice_data)
        #写入Json文件
        with open('slices.json','w') as wsf:
            json.dump(slice_datas,wsf,ensure_ascii=False)
        with open('id_slices.txt','w') as kf:
            kf.write(str(slice_id))
        tag = 0

    except IOError:

        tag = -1

    return{"message":"create new slice","data":slice_data,"tag":tag}

#选择主播
@app.get('/streamer/{streamer_id}')
def get_streamers(streamer_id:int):
    persons = []
    with open('streamers.json','r') as sf:
        streamers=json.load(sf)

    if streamer_id > 0 :
        for index, streamer in enumerate(streamers['streamers']):
            if streamer_id == streamer['id']:
                persons.append(streamer)
    else:
        persons.append(streamers['streamers'])

    return {"message":"get streamer info",'data':persons}

#创建新直播间
#直播间的数据结构
class Stream_Room(BaseModel):
    room_name: str = '直播间'
    streamer: Union[LiveStreamer,None] = None
    product_ids: Union[List,None] = None
    stream_status: str = "down"
    streamer_status: str = "draft"

@app.post("/rooms/creat")
async def new_room(room: Stream_Room):
    room_id = 0
    tag = -1
    with open('id_keys.txt','r') as keyf:
        file = keyf.read()
        if len(file) > 0:
            key = int(file)
        else:
            key = 0

        room_id = key + 1
    #保存房间信息
    if room_id > 0:
        room_data = {}
        room_data.update({"room_id":room_id})
        room_data.update({"room_name":room.room_name, "streamer_id":room.streamer.id,"streamer_name":room.streamer.name,"streamer_pic":room.streamer.picPath})
        room_data.update({"product_ids":room.product_ids, "stream_status":room.stream_status,"streamer_status":room.streamer_status})
        try:
            with open('show_room.json','r',encoding='utf-8') as jf:
                file = jf.read()
                if len(file)>0:
                    room_datas=json.loads(file,strict=False)
                else:
                    room_datas = {"room_datas":[]}

                room_datas['room_datas'].append(room_data)
                print(room_datas)
            with open('show_room.json','w') as wf:
                json.dump(room_datas,wf,ensure_ascii=False)
                wf.close()
            with open('id_keys.txt','w') as kf:
                kf.write(str(room_id))
                tag = 0
        except IOError:
            tag = -1
    return {"message":"append new room","data":room_data,"tag":tag}
#修改直播间内容

@app.post("/rooms/update/{room_id}")
async def update_room(room_id:int, room: Stream_Room):
    return {"message":"update room info"}


#查询直播间
@app.get("/rooms/{room_id}")
async def get_rooms(room_id:int):
    rooms = []
    with open('show_room.txt', 'r') as f:
        for line in f:
          strdata = '{'+line+'}'
          dictdata = json.loads(strdata)
          rooms.append(dictdata)
    datas =[]
    if room_id==0 or room_id is None:
        datas = rooms
    else:
        for index, room in enumerate(rooms):
            in_id = room['room_id']
            if room_id == in_id:
                datas.append(room)

    return {"message":"get rooms info",'rooms_data': datas}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app='main:app', host="127.0.0.1", port=3005, reload=True)