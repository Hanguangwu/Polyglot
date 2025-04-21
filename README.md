# Polyglot

语言学习平台，包括单词、聊天、写作和复习四大部分。

本地部署需要配置前端和后端的.env文件。

启动前端：

```
cd frontend
npm install
npm run dev
```

启动后端：

```
cd backend
pip install -r requirements.txt
python main.py
```

前端.env文件内容如下所示：

```
BACKEND_BASE_URL=https://localhost:3000
```

后端.env文件内容如下所示：

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=Polyglot
SECRET_KEY=xxxxxxxxxxx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CHATANYWHERE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
CHATANYWHERE_BASE_URL=https://api.chatanywhere.tech
```


