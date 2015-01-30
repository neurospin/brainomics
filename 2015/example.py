import numpy as np

from sklearn.cross_validation import LeaveOneLabelOut, cross_val_score
from sklearn.linear_model import LogisticRegression
from nilearn.datasets import fetch_localizer_contrasts
from nilearn.input_data import NiftiMasker

# fetch the specified tasks from the localizer database

tasks = [
    'horizontal checkerboard',
    'vertical checkerboard',
    'sentence reading',
    'calculation (auditory cue)',
    'calculation (visual cue)',
    'left button press (auditory cue)',
    'left button press (visual cue)',
    'right button press (auditory cue)',
    'right button press (visual cue)',
]

localizer_data = fetch_localizer_contrasts(tasks, get_tmaps=True)
images = np.array(localizer_data['tmaps'])

# we denote the statistical maps as X, and the target to predict as y
masker = NiftiMasker(standardize=True, memory='cache')
X = masker.fit_transform(images)
y = np.array(['calc' if 'calculation' in img else 'non-calc' for img in images])

# we perform a leave-one subject out cross validation
cv = LeaveOneLabelOut(ext_vars.subject_id.values)

# we use a LogisticRegression classifier with default parameters
clf = LogisticRegression()

scores = cross_val_score(clf, X, y, cv=cv, n_jobs=-1, verbose=1)
print 'scores mean=%.02f, std=%.02f' % (np.mean(scores), np.std(scores))
