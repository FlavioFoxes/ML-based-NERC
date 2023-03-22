# ML-based-NERC

To run the CRF program:

```
python3 session2/extract-features.py data/train > train_crf.feat
```
```
python3 session2/train-crf.py model.crf < train_crf.feat
```
```
python3 session2/extract-features.py data/devel > devel_crf.feat
```
```
python3 session2/predict.py model.crf <devel_crf.feat >devel_crf.out
```
```
python3 util/evaluator.py NER data/devel devel_crf.out
```

To run the MEM model:


```
python3 session2/extract-features.py data/train > train_mem.feat
```
```
cat train.feat | cut -f5- | grep -v ^$ > train.mem.feat
```
```
./megam-64.opt -quiet -nc -nobias multiclass train.mem.feat > model.mem
```
```
python3 session2/extract-features.py data/devel > devel_mem.feat
```
```
python3 session2/predict.py model.mem <devel_mem.feat >devel_mem.out
```
```
python3 util/evaluator.py NER data/devel devel_mem.out
```
