# ML-based-NERC

To run the CRF program:

```
python3 session2/extract-features.py data/train > train.feat
```
```
python3 session2/train-crf.py model.crf < train.feat
```
```
python3 session2/extract-features.py data/devel > devel.feat
```
```
python3 session2/predict.py model.mem <devel.feat >devel.out
```
```
python3 util/evaluator.py data/devel devel.out
```
