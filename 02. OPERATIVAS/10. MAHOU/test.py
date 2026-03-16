import pyboof as pb

detector = pb.FactoryFiducial(np_dtype="uint8").createDataMatrixDetector()

image = pb.load_image("codigo.png", np_dtype="uint8")
detections = detector.detect(image)

for d in detections:
    print("Código:", d.message)
