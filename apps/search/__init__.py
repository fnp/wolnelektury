import lucene
JVM = lucene.initVM(lucene.CLASSPATH)
from index import Index, Search, ReusableIndex, MultiSearch, SearchResult
