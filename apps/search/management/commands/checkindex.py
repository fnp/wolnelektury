
from django.core.management.base import BaseCommand
from search import IndexChecker

class Command(BaseCommand):
    help = 'Check Lucene search index'
    args = ''

    def handle(self, *args, **opts):
        checker = IndexChecker()
        status = checker.check()
        if status.clean:
            print "No problems found."
        else:
            if status.missingSegments:
                print "Unable to locate."
            print "Number of bad segments: %d / %d (max segment name is %d)" % \
                (status.numBadSegments, status.numSegments, status.maxSegmentName)
            print "Total lost documents (due to bad segments) %d" % status.totLoseDocCount
            if not status.validCounter:
                print "Segment counter is not valid."
        
