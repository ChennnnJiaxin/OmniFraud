# %%
classes = ['冒充公检法及政府机关类', '冒充军警购物类诈骗', '冒充电商物流客服类', '冒充领导、熟人类', '无风险',
       '网络婚恋、交友类', '网黑案件', '虚假信用服务类', '虚假网络投资理财类', '虚假购物、服务类']
# test_text = "您好，抖音上发现有人提供替考驾驶证服务，每科仅需1400元，微信号为wei1in12345，如有需要请联系，我们保证快速通过考试。"
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer, BertForSequenceClassification
import torch

class MsgClsModel:
# %%

    # Use Huawei Nezha model
    def __init__(self):
        self.lb = LabelEncoder()
        self.lb.classes_ = classes
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        self.model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=len(classes)).to(device)
        import os
        if not os.path.exists(r"model/final_model.pth"):
            print("Model not found, downloading...")
            import requests
            url = "https://dlink.host/1drv/aHR0cHM6Ly8xZHJ2Lm1zL3UvYy82YWE4YmQ4MzYxZWQ0NTkwL0VYT1F5WktPTnJSUG1vdENncVVodVI4QjZ4MV9uMjVfMDhFTGdlOHNURF9Fcnc_ZT05ZXB4WE4.pth"
            response = requests.get(url)
            os.makedirs("model", exist_ok=True)
            with open("model/final_model.pth", "wb") as f:
                f.write(response.content)
        # Use Huawei Nezha model
        self.model.load_state_dict(torch.load(r"model/final_model.pth", map_location=device))
        if torch.cuda.is_available():
            self.model = self.model.cuda()
    
    def encode_texts(self, texts):
        return self.tokenizer(
            texts,
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='pt',
        )
        
    # %%
    def predict(self, test_text):
        output = self.model(**self.encode_texts([test_text]).to(device))
        output = output.logits
        output = torch.softmax(output, dim=1)
        output = output.cpu().detach().numpy()
        output = output[0]
        output = list(zip(self.lb.classes_, output))
        output = sorted(output, key=lambda x: x[1], reverse=True)
        return output

# %%
if __name__ == "__main__":
    model = MsgClsModel()
    test_text = "【顺丰】尊敬的客户，您使用顺丰的频率较高，现赠送您暖风扇一台，请添加支付宝好友进行登记领取。"
    print(model.predict(test_text))
