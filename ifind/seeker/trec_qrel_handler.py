__author__ = 'leifos'


from ifind.seeker.common_helpers import file_exists
from ifind.seeker.common_helpers import AutoVivification
from ifind.seeker.topic_document_file_handler import TopicDocumentFileHandler

class TrecQrelHandler(TopicDocumentFileHandler):

    def __init__(self, filename=None):
        super(TrecQrelHandler, self).__init__(filename)

    def _put_in_line(self, line):
        '''
        Possibly the worse way ever to parse through a line. Please someone fix this code.
        For TREC QREL the Format is:
            Topic Iteration Document Judgement
            Iteration is not used.
        '''
        parts = line.partition(' ')
        topic = parts[0]
        parts = parts[2].partition(' ')
        parts = parts[2].partition(' ')
        doc = parts[0]
        judgement = '0' + parts[2].strip()
        if topic and doc:
            self.data[topic][doc] =  int(judgement)

    def _get_out_line(self, topic, doc):
        # outputs the topic document and value as the TREC QREL Format with iteration default to zero
        return "%s 0 %s %d\n" % (topic, doc, self.data[topic][doc])
    
    

