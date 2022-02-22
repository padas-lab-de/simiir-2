__author__ = 'Kojayboy'


class RetrievabilityMeasure(object):

	doc_list = {}
	b = 0.0
	c = 100

	def __init__(self, b, c):
		self.b = b
		self.c = c
		self.doc_list = {} ## lolwut. without this, all instances share the same dictionary :/

	def __str__(self):
		if self.b > 0.0:
			return "Gravity Measure. Beta = %f Cutoff = %d" % (self.b, self.c)
		else:
			return "Cumulative Measure. Cutoff = %d" % (self.c)

	def process_document(self, docid, rank):
		if rank > self.c:
			return
		#print 'Processing document %s, at rank %d' % (docid,rank)
		#print str(self)

		score = self.get_retrievability_score(docid)
		if self.b > 0.0:
			self.doc_list[docid] = score + (1.0 / pow(float(rank), self.b))
		else:
			self.doc_list[docid] = score + 1


	def get_retrievability_score(self, docid):
		try:
			return self.doc_list[docid]
		except KeyError:
			return 0


class RetrievabilityRuler(object):

	measures_list = []
	doc_list = []

	def __init__(self, doc_list):
		self.doc_list = doc_list

	def add_measure(self, RetrievabilityMeasure):
		self.measures_list.append(RetrievabilityMeasure)

	def process_document(self, docid, rank):
		'''
		defer call to retmeasure processdoc
		'''
		for measure in self.measures_list:
			measure.process_document(docid, rank)

	def save_file(self, filename, titles):
		'''
		for each doc in doc list, output scores. output to file
		'''

		file = open(filename, 'w')

		if titles:
			file.write(self.get_titles())
		for doc in self.doc_list:
			file.write("%s " % (doc))
			for score in self.get_scores(doc):
				if type(score) == type(0.0):
					file.write("%f " % score)
				else:
					file.write("%d " % score)
			file.write("\n")
		file.close()


	def get_scores(self, docid):
		'''
		return list of scores for each retmeasure on a given docid
		'''
		score_list = []
		for measure in self.measures_list:
			score_list.append(measure.get_retrievability_score(docid))
		return score_list

	def get_titles(self):
		titles = "DOCID"
		for measure in self.measures_list:
			titles = titles + " " + str(measure)
		titles = titles + "\n"
		return titles

