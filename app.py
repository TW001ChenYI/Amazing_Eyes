import os

import requests
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'


# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Process file and predict his label
@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        file = request.files['image']
        fullname = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(fullname)
        car=request.values['traffic']
        if car=="A":
            car2='汽車'
        elif car=="B":
            car2='機車'
        result=os.popen("docker run -it --rm -v $(pwd)/uploads:/data:ro openalpr "+file.filename+" --config ./dataset/tw.conf")
        fin=result.read()
        q=[i for i in range(0,fin.count("plate"))]

        if "No license plates found." in fin:
            print("No license plates found.")
        else:
        # print(type(fin.count("plate")))
            if fin.count("plate")==1:
                q[0]=fin[:len(fin)-1]
                print(q[0])
            else:            
                for i in range(0,fin.count("plate")) :
                    # q[i]
                    # y=f"plate{i}"
                    q[i]=fin[fin.find(str(f"plate{i}")):fin.find(str(f"plate{i+1}"))]
                    print(q[i])
        
        for i in range(0,fin.count("plate")) :
            k=0
            x=[]
            n=[j for j in range(0,fin.count("plate"))]
            for m in q[i]:
                if(m=="-"):
                    x.append(fin[k+2:k+9])
                    break
                k+=1
            po=list(x[0])
            b='-'
            o2=po.insert(3,b)
            po2=''.join(po)

            url=f"https://od.moi.gov.tw/adm/veh/query_veh?_m=query&vehType={car}&vehNumber={po2}"

            re=requests.get(url)
            with open('./csv_data/data.csv','wb') as f:
                f.write(re.content)
            import pandas as pd
            test=pd.read_csv('./csv_data/data.csv',encoding='BIG5')
            test1=test.drop(columns=['注意事項：「下列失車查詢結果以回傳該查詢時間有效，失車查詢結果會依現況隨時做資料更新」。'])
            # print(str(test1.index[1][2]))
            if test1.index[1][2]=="查無資料":
                test1="經查詢，目前為非失竊車輛"
            else:
                test1=test1.index[1][2]
        return render_template('predict.html', image_file_name=file.filename,fin=po2,car=car2,test=test1)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)
    app.debug = True
