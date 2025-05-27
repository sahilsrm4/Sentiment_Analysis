def give_paragraph_analysis(pipeline,paragraph):
  classifier = pipeline('text-classification',model = 'distilbert-base-uncased-finetuned-sst-2-english')
  res = classifier(paragraph)
  return res