# Saved face model

tools/video_qa.py looks here first for face_detection_yunet_2023mar.onnx (OpenCV Zoo YuNet, MIT licence, sha256
8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4), then in ~/.cache/pnf-video-models/, then downloads it.
Cloud runs cannot download it, so until a copy is saved here their face selftest is skipped with a note. A real video's
face check never skips: without the model it fails as "could not run". A run on Todd's PC can copy the cached file here.
