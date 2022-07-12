from flask import Flask, render_template, request,flash
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField,SubmitField
from wtforms import validators
import pickle

app = Flask(__name__)
app.secret_key = 'xiejialong213@163.com'

path = '.'

with open(path + '/static/dip_group2.pkl', 'rb') as fid:
    dip_group = pickle.load(fid)
with open(path + '/static/手术组.pkl', 'rb') as fid:
    手术组 = pickle.load(fid)
with open(path + '/static/治疗组.pkl', 'rb') as fid:
    治疗组 = pickle.load(fid)
with open(path + '/static/诊断组.pkl', 'rb') as fid:
    诊断组 = pickle.load(fid)


with open(path + '/static/ICD_10_ICD_yb.pkl', 'rb') as fid:
    ICD_10_ICD_yb = pickle.load(fid)

with open(path + '/static/ICD_9_ICD_yb.pkl', 'rb') as fid:
    ICD_9_ICD_yb = pickle.load(fid)



def pp_zd(x):
    try:
        return(ICD_10_ICD_yb.loc[x,'诊断编码医保2'])
    except:
        return ''

def pp_ss(x):
    try:
        return(ICD_9_ICD_yb.loc[x,'手术编码医保2'])
    except:
        return ''




def get_dip(zyzd,sscz,bah):
#     global a
    try:
        zyzd4 = zyzd[:5].upper() #4位编码 I21.1
        zyzd3 = zyzd[:3].upper() #3位编码 I21
        zyzd1 = zyzd[:1].upper() #1位编码 I
        sscz = pd.Series(sscz).dropna().values
        dips = dip_group.loc[dip_group.主要诊断.isin([zyzd3,zyzd4,zyzd1])]  #主要诊断为[I21.1 I21 I]的所有分组
        if len(sscz)==0:
            return(dips.loc[dips.组类型=='内科组',:].index.values[0])
        else:
            # [ '手术组', '治疗组', '诊断组']:
            dip_ssz = dips.loc[dips.组类型=='手术组',:]
#             a = dip_ssz
            for i in dip_ssz.index:
                # [[A,C],[A,D],[B,C],[B,D]] 中任意 一个元素 是否包含于 [A,X,X,X,B]
                if pd.Series(dip_ssz.loc[i,'手术操作代码']).apply(lambda x:pd.Series(x).isin(sscz).all()).any():
                    return i
            if sum(pd.Series([['手术组']]). isin( dip_ssz.手术操作代码) & pd.Series(sscz).isin(手术组).any())>0:
                return dip_ssz.loc[dip_ssz.组类别=='综合组',:].index.values[0]

            dip_ssz = dips.loc[dips.组类型=='治疗组',:]
            for i in dip_ssz.index:
                # [[A,C],[A,D],[B,C],[B,D]] 中任意 一个元素 是否包含于 [A,X,X,X,B]
                if pd.Series(dip_ssz.loc[i,'手术操作代码']).apply(lambda x:pd.Series(x).isin(sscz).all()).any():
                    return i
            if sum(pd.Series([['治疗组']]). isin( dip_ssz.手术操作代码) & pd.Series(sscz).isin(治疗组).any())>0:
                return dip_ssz.loc[dip_ssz.组类别=='综合组',:].index.values[0]

            dip_ssz = dips.loc[dips.组类型=='诊断组',:]
            for i in dip_ssz.index:
                # [[A,C],[A,D],[B,C],[B,D]] 中任意 一个元素 是否包含于 [A,X,X,X,B]
                if pd.Series(dip_ssz.loc[i,'手术操作代码']).apply(lambda x:pd.Series(x).isin(sscz).all()).any():
                    return i
            if sum(pd.Series([['诊断组']]). isin( dip_ssz.手术操作代码) & pd.Series(sscz).isin(诊断组).any())>0:
                return dip_ssz.loc[dip_ssz.组类别=='综合组',:].index.values[0]
            return 'Z9999'
    except:
        #print(bah)
        return('xxxx')






# 使用WTF实现表单 自定义表单类
class LoginForm(FlaskForm):
    # 'Marital','Site', 'Tumor_size','Race','Chemotherapy','Sex','Age','Surgery'

    diagnosis = StringField('主要诊断编码(完整长度):',validators=[validators.DataRequired()])
    operation = StringField('手术操作编码(多个用逗号隔开):')
    fenzu = StringField('分组:' )
    fenzhi = StringField('分值:' )
    zhuyaozhenduan = StringField('主要诊断:' )
    shoushucaozuo = StringField('手术操作:' )
    Submit = SubmitField('查询')

# mod = joblib.load('gbdt_model.pkl')


@app.route('/', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    # 1.判断请求方式
    if request.method == 'POST':
        # 2.获取参数
        diagnosis = request.form.get('diagnosis').replace(' ','')
        operation = request.form.get('operation').replace('，',',')

        operations = []
        # 3.校验参数
        if login_form.validate_on_submit():
            #print(diagnosis,operations)
            diagnosis = pp_zd(diagnosis)
            if ',' in operation:
                for i in operation.split(','):
                    operations.append(pp_ss(i))
            elif operation!='':
                operations=[pp_ss(operation)]
            #print(diagnosis,operations)
            fzu = get_dip(diagnosis,operations,'101') #分组
            fzhi = dip_group.loc[fzu,'分值']
            zd = dip_group.loc[fzu,'主要诊断名称']
            cz = dip_group.loc[fzu,'手术操作名称']
            login_form.fenzu.data = fzu
            login_form.fenzhi.data = '%.2f' % fzhi
            login_form.zhuyaozhenduan.data = zd
            login_form.shoushucaozuo.data = cz
            return render_template('index.html', form=login_form)

        else:
            # flash('error')
            return 'ERROR: 诊断不能为空!'



    return render_template('index.html',form=login_form)


if __name__ == '__main__':
    app.run()