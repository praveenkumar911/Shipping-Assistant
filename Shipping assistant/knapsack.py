from flask import Flask,render_template,request,redirect
import pymongo
import pandas as pd
app=Flask(__name__)
myclient=pymongo.MongoClient("mongodb://localhost:27017/")
mydb=myclient["knapsack"]
mycol=mydb['shipment']

@app.route('/',methods=['GET','POST'])
def login():
    data={}
    if request.method=='POST':
        data['wt']=request.form['wt']
        data['w_']=request.form['w_']
        data['v_']=request.form['v_']
        data['s_date']=request.form['dt']
        data['s_lat']=request.form['lt']
        data['s_long']=request.form['lot']
        data['s_dist_origin']=request.form['sdto']
        wt=float(data['wt'])*1000
        w_=data['w_'].split(',')
        w=[]
        k=0
        for i in w_:
            w.append(float(i))
            k+=float(i)
        data['s_weight_tot']=k/1000
        v=[]
        data['s_value_tot']=0
        v_=data['v_'].split(',')
        for j in v_ :
            v.append(float(j))
            data['s_value_tot']+=float(j)
        n=len(w)
        data['s_nitems']=n
        data['t']=ship(n,w,v,wt)
        data['item_list']=item_list
        data['s_eff']=round(float(data['s_weight_tot'])/float(data['wt'])*100)
        data['s_costperkm']=float(data['s_value_tot'])/float(data['s_dist_origin'])
        k=mycol.aggregate([
            {  '$group':{'_id':"",
                         'histroic_weight':{'$sum':'$s_weight_tot'}},
             }
            ])
        for i in k:
            data['histroic_wht']=i['histroic_weight']
        m=mycol.aggregate([
             {  '$group':{'_id':"",
                          'total_cost':{'$sum':'$s_costperkm'}},
              }
             ])
        for j in m:
             data['total_cst']=j['total_cost']
        l=mycol.aggregate([
            {  '$group':{'_id':"",
                         'total_shipped':{'$sum':'$s_nitems'}},
             }
            ])
        for s in l:
            data['tot_shiped']=s['total_shipped']
        o=mycol.find().sort('s_costperkm',-1)
        for i in o:
            data['best_case']=i['s_costperkm']
        l=mycol.find().sort('s_costperkm',1)
        for j in l:
            data['worst_case']=i['s_costperkm']
        mydb.shipment.insert_one(data)
        return redirect('/op')
    else:
        return render_template('login.html')
def ship(n,w,v,wt):
    global total_value,item_list
    if n==0 or wt==0:
        return str(total_value)
    elif w[n-1]>wt:                                #function for calculating item list and total value
        return ship(n-1,w,v,wt)
    else:
        total_value=total_value+v[n-1]
        item_list.append(w[n-1])
        return ship(n,w,v,wt-w[n-1])
    return str(total_value)
total_value=0
item_list=[]
@app.route('/db')
def db():
    k=mycol.find()
    k=list(k)
    df=pd.DataFrame(k)
    html=df.to_html()
    tf=open(r'C:\Users\prave\iiit\templates/index.html','w')
    tf.write(html)
    tf.close()
    return render_template('index.html')
@app.route('/op')
def op():
    x=mycol.find({},{'worst_case','best_case','histroic_wht','tot_shiped','total_cst','item_list','wt'})
    df=pd.DataFrame(x)
    html=df.to_html()
    tf=open(r'C:\Users\prave\iiit\templates/mo.html','w')
    tf.write(html)
    tf.close()
    return render_template('mo.html')
def kp():
    import matplotlib.pyplot as plt
    plt.scatter(x=data['s_lat'],y=['s_long'])
    plt.show()
if __name__=='__main__':
    app.run(debug=False)

