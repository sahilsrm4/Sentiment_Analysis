
def give_analysis(comments,classifier):
     print("Analyzing Comments...")
     res = classifier(comments)
     for i in range(len(comments)):
          print(res[i],' -> ',comments[i])
     labels = [r['label'] for r in res]
     neutral = labels.count('LABEL_1')
     positive = labels.count('LABEL_2')
     negative = labels.count('LABEL_0')
     print('Comments Analyzed')
     return {'Positive':positive,'Neutral':neutral,'Negative':negative}