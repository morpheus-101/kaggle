# -*- coding: utf-8 -*-
"""titanic_ml.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/127dSFl4e7gKs2hP5hGNrJM6iQUgfIVCN

Loading data
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

plt.style.use('ggplot')

train=pd.read_csv('/content/train.csv')
test=pd.read_csv('/content/test.csv')
full_data=pd.concat([train,test],ignore_index=True)

full_data.head()

"""Data cleaning"""

full_data.isnull().sum()

full_data.shape

full_data.Embarked.mode()

full_data['Embarked'].fillna('S',inplace=True)

full_data[full_data.Fare.isnull()]
full_data.Fare.fillna(full_data[full_data.Pclass==3]['Fare'].median(),inplace=True)

full_data.isna().sum()

def fill_missing_ages(df):
    ages_missing_index = df[df['Age'].isnull()].index
    for idx in ages_missing_index:
        row = df.loc[idx, :]
        median_age = df['Age'].median()
        media_age_pred = df[(df['Pclass'] == row['Pclass']) & (df['SibSp'] == row['SibSp']) & (df['Parch'] == row['Parch'])]['Age'].median()
        if np.isnan(media_age_pred):
            df.loc[idx, 'Age'] = median_age
        else:
            df.loc[idx, 'Age'] = media_age_pred

print('Median age before filling missing values: ', full_data['Age'].median())
fill_missing_ages(full_data)
print('Median age after filling missing values: ', full_data['Age'].median())

full_data.isna().sum()

df = full_data

for i in df.index:
    if pd.isnull(df.at[i, 'Cabin']) :
        df.at[i, 'Cabin'] = 0
    else:
        df.at[i, 'Cabin'] = 1

for i in df.index:
    if df.at[i, 'Sex']=="male" :
        df.at[i, 'Sex'] = 1
    else:
        df.at[i, 'Sex'] = 0

for i in df.index:
    if df.at[i, 'Embarked']=="C" :
        df.at[i, 'Embarked'] = 0
    elif df.at[i, 'Embarked']=="Q" :
        df.at[i, 'Embarked'] = 1    
    else:
        df.at[i, 'Embarked'] = 2

df.head()

df = df.drop(['PassengerId', 'Name', 'Ticket'], axis = 1)
df.head()

from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC

models=[KNeighborsClassifier(),LogisticRegression(),GaussianNB(),DecisionTreeClassifier(),RandomForestClassifier(),
       GradientBoostingClassifier(),SVC()]

import numpy as np
from sklearn.model_selection import train_test_split
X = df.iloc[:891]
X = X[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Cabin', 'Embarked']]
y = df.Survived[:891]

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit(X).transform(X)

X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size = 0.20, random_state=42)

names=['KNN','LR','NB','Tree','RF','GDBT','SVM']
for name, model in zip(names,models):
    score=cross_val_score(model,X_train,y_train,cv=5)
    print("{}:{},{}".format(name,score.mean(),score))

model = GradientBoostingClassifier()

model.fit(X,y)

model.feature_importances_

X.columns

fi=pd.DataFrame({'importance':model.feature_importances_},index=X.columns)

fi.sort_values('importance',ascending=False)

fi.sort_values('importance',ascending=False).plot.bar(figsize=(11,7))
plt.xticks(rotation=30)
plt.title('Feature Importance',size='x-large')

"""Hyperparameter tuning"""

from sklearn.model_selection import GridSearchCV

"""KNN"""

param_grid={'n_neighbors':[1,2,3,4,5,6,7,8,9]}
grid_search=GridSearchCV(KNeighborsClassifier(),param_grid,cv=5)
grid_search.fit(X_train,y_train)
grid_search.best_params_,grid_search.best_score_

"""Logistic Regression"""

param_grid={'C':[0.01,0.1,1,10]}
grid_search=GridSearchCV(LogisticRegression(),param_grid,cv=5)
grid_search.fit(X_train,y_train)
grid_search.best_params_,grid_search.best_score_

param_grid={'C':[0.04,0.06,0.08,0.1,0.12,0.14]}
grid_search=GridSearchCV(LogisticRegression(),param_grid,cv=5)
grid_search.fit(X_train,y_train)
grid_search.best_params_,grid_search.best_score_

"""SVM"""

param_grid={'C':[0.01,0.1,1,10],'gamma':[0.01,0.1,1,10]}
grid_search=GridSearchCV(SVC(),param_grid,cv=5)
grid_search.fit(X_train,y_train)
grid_search.best_params_,grid_search.best_score_

param_grid={'C':[2,4,6,8,10,12,14],'gamma':[0.008,0.01,0.012,0.015,0.02]}
grid_search=GridSearchCV(SVC(),param_grid,cv=5)
grid_search.fit(X_train,y_train)
grid_search.best_params_,grid_search.best_score_

param_grid={'n_estimators':[30,50,80,120,200],'learning_rate':[0.05,0.1,0.5,1],'max_depth':[1,2,3,4,5]}
grid_search=GridSearchCV(GradientBoostingClassifier(),param_grid,cv=5)
grid_search.fit(X_train,y_train)
grid_search.best_params_,grid_search.best_score_

"""Ensemble methods

Bagging
"""

from sklearn.ensemble import BaggingClassifier
bagging=BaggingClassifier(LogisticRegression(C=0.06),n_estimators=100)

"""Voting"""

from sklearn.ensemble import VotingClassifier

clf1=LogisticRegression(C=0.01)
clf2=RandomForestClassifier(n_estimators=500)
clf3=GradientBoostingClassifier(n_estimators=30,learning_rate=0.5,max_depth=2)
clf4=SVC(C=10,gamma=0.02,probability=True)
clf5=KNeighborsClassifier(n_neighbors=8)

eclf_hard=VotingClassifier(estimators=[('LR',clf1),('RF',clf2),('GDBT',clf3),('SVM',clf4),('KNN',clf5)])

# add weights
eclfW_hard=VotingClassifier(estimators=[('LR',clf1),('RF',clf2),('GDBT',clf3),('SVM',clf4),('KNN',clf5)],weights=[1,1,2,2,1])

# soft voting
eclf_soft=VotingClassifier(estimators=[('LR',clf1),('RF',clf2),('GDBT',clf3),('SVM',clf4),('KNN',clf5)],voting='soft')

# add weights
eclfW_soft=VotingClassifier(estimators=[('LR',clf1),('RF',clf2),('GDBT',clf3),('SVM',clf4),('KNN',clf5)],voting='soft',weights=[1,1,2,2,1])

models=[KNeighborsClassifier(n_neighbors=8),LogisticRegression(C=0.06),GaussianNB(),DecisionTreeClassifier(),RandomForestClassifier(n_estimators=500),
        GradientBoostingClassifier(n_estimators=120,learning_rate=0.12,max_depth=4),SVC(C=4,gamma=0.015),
        eclf_hard,eclf_soft,eclfW_hard,eclfW_soft,bagging]

names=['KNN','LR','NB','CART','RF','GBT','SVM','VC_hard','VC_soft','VCW_hard','VCW_soft','Bagging']
for name,model in zip(names,models):
    score=cross_val_score(model,X_scaled,y,cv=5)
    print("{}: {},{}".format(name,score.mean(),score))

clf = GradientBoostingClassifier(random_state=0, n_estimators=30, max_depth=2, learning_rate=0.5)
clf.fit(X_train, y_train)
clf.predict(X_val)
clf.score(X_val, y_val)

X_test = df.iloc[891:]
X_test = X_test[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Cabin', 'Embarked']]

s = StandardScaler()
X_test_scaled = s.fit(X_test).transform(X_test)

pred = clf.predict(X_test_scaled)
tt=pd.DataFrame({'PassengerId':test.PassengerId,'Survived':pred})
tt.to_csv('result_3.csv',index=False)

sub = pd.read_csv('/content/result_3.csv')

sub.dtypes

train.dtypes

sub = sub['Survived'].astype(int)

sub.dtypes

tt=pd.DataFrame({'PassengerId':test.PassengerId,'Survived':sub})
tt.to_csv('result_new.csv',index=False)
