import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

data = pd.read_csv('Test_2022_08_30\\ZH026_2341_holes_checking_revisit_all_Images_inverted.csv')

print(data.head())
sns.histplot(data=data, x='NoDefects', stat="percent", bins=20)
# ax = data['NoDefects'].plot.hist(bins=25, alpha=0.5)

dataBool = data.copy()

# if NewLabel (humanLabel) doesnt exist we insert a default NoDefect, if it exists, comment the lines

'''
n_images = dataBool.shape[0]
human_label = ['NoDefects'] * n_images
dataBool.insert(2, 'NewLabel', human_label, True)
'''

dataBool.drop(columns=['Location', 'Defects', 'NoDefects'], axis=1, inplace=True)

# print(dataBool)

dataBool['Label'] = dataBool['Label'].map({'Defects': 1, 'NoDefects': 0})
dataBool['NewLabel'] = dataBool['NewLabel'].map({'Defects': 1, 'NoDefects': 0})

y_pred = dataBool['Label'].values
y_true = dataBool['NewLabel'].values

print(len(y_true), len(y_pred))

cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
print(cm)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])
# disp.plot()
plt.show()

