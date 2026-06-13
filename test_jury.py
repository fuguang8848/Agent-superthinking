import sys
sys.path.insert(0, 'src')
from super_thinking.core.jury import Jury

j = Jury()
r = j.think('AI对教育的影响')
print('experts:', r.analysis_metadata.get('experts_used'))
print('type:', r.analysis_metadata.get('question_type'))
print('outputs:', len(r.outputs))