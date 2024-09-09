import _thread as thread
import json
import ssl
import websocket
import configparser
from wsPram import Ws_Param
from KnowledgeRetriever import KnowledgeRetriever

class GptMsg():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini', encoding='utf-8')
        self.APPID = self.config['DEFAULT']['APPID']
        self.APISecret =self. config['DEFAULT']['APISecret']
        self.APIKey = self.config['DEFAULT']['APIKey']
 
        self.gpt_url = 'wss://spark-api.xf-yun.com/v1.1/chat'
        self.domain='general' #lite
        self.msg = ''
        self.question = ''
 
        self.txt = self.config['DEFAULT']['TXT']
        self.name = self.config['DEFAULT']['NAME']
        self.history_text = [{"role":"system","content": self.txt}]
        self.retriever = KnowledgeRetriever()
        print('gpt初始化成功')
    def send_msg(self, question):
        # 获取url
        wsParam = Ws_Param(self.APPID, self.APIKey, self.APISecret, self.gpt_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ancillary_info =KnowledgeRetriever.records_to_str(self.retriever.retrieve_str(question))
        print(ancillary_info)
        # 消息加入
        prompt="""
请你扮演一名人工智能辅助医生，回答用户的医疗相关问题。
用户将会自然地和你交流，同时系统将根据用户的问题检索相关辅助信息并提供给你。请你运用你自身知识和辅助信息，为用户提供详细的医疗咨询。

相关辅助信息如下:{ancillary_info}

用户消息如下:{question}

请注意，你的回答应该是有逻辑的，详细的，符合医学常识的，符合正常对话逻辑的（不要被辅助信息影响），注意联系上下文；
辅助信息由系统提供，用户的问题可能不完全匹配辅助信息，你需要自己判断，不应该完全依赖于辅助信息。用户不应该知道辅助信息的存在。
请更关注用户消息，而非辅助信息。
""".format(ancillary_info=ancillary_info, question=question)
        self.question = question
        ques_json = {"role": "user", "content": prompt}
        self.history_text.append(ques_json)
        self.msg=''
        # 发送消息
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_open=self.on_open)
        ws.appid = self.APPID
        ws.domain = self.domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
 
    # 收到websocket错误的处理
    def on_error(self, ws, error):
        print("### error:", error)
 
    # 收到websocket关闭的处理
    def on_close(self, ws, *args):
        # print("### closed ###")
        pass
 
    # 收到websocket连接建立的处理
    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))
 
    def run(self, ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, domain=ws.domain))
        ws.send(data)
 
    def gen_params(self, appid, domain):
        # print(window.history_text)
        if len(self.history_text) >= 128:
            print("pop handle")
            self.history_text.pop(1)
            self.history_text.pop(2)
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234",
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": self.history_text
                }
            }
        }
        return data
 
    # 收到websocket消息的处理
    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            #删除最后一个用户消息
            self.history_text.pop()
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.msg+=content
            if status == 2:
                #修改最后一个用户消息
                self.history_text[-1] = self.toText("user",self.question)
                self.history_text.append(self.toText("assistant",self.msg))
                ws.close()
    
    def toText(self,role,content):
        return {'role':role,'content':content}
 
if __name__ == '__main__':
    gpt = GptMsg()
    while True:
        question = input('user:')
        gpt.send_msg(question)
        print('GPT:'+gpt.msg)