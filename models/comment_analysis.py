
def give_analysis(comments,pipeline):
     classifier = pipeline('sentiment-analysis', model = 'cardiffnlp/twitter-roberta-base-sentiment')
     res = classifier(comments)
     
     labels = [r['label'] for r in res]
     neutral = labels.count('LABEL_1')
     positive = labels.count('LABEL_2')
     negative = labels.count('LABEL_0')
     
     return {'Positive:':positive,'Neutral':neutral,'Negative':negative}