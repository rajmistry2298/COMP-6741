import pandas as pd 
  
data1 = pd.read_csv("Data.csv",encoding= 'latin1')
data2 = pd.read_csv("DES.csv",encoding= 'latin1') 
  
#merge function by setting how='left' 
output = pd.merge(data1, data2, on='Course ID', how='left')
#print(output2)
output.to_csv("output.csv")

data3 = pd.read_csv("output.csv",encoding= 'latin1')
data4 = pd.read_csv("WEBSITE.csv",encoding= 'latin1')
output1 = pd.merge(data3, data4, on='Course ID', how='left')
output1.to_csv("course.csv")