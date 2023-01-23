import os 
import random

import vlogging
import numpy as np
import tqdm
import tqdm

import facecctv_ai.config
import facecctv_ai.data_generator
import facecctv_ai.detections
import facecctv_ai.geometry
import facecctv_ai.models
import facecctv_ai.processing
import facecctv_ai.utils

def log_data_batch(data_generator, logger):

      for index in range(8):

            images, labels = next(data_generator)

            images = [image * 255 for image in images]
            images = [facecctv_ai.processing.scale_image(image, 100) for image in images]
            logger.info(vlogging.VisualRecord("image batch", images, str(labels)))

def log_crop_prediction(data_generator, logger):

      model = facecctv_ai.models.get_vgg_model(facecctv_ai.config.image_shape)
      model.load_weights(facecctv_ai.config.model_path)

      for index in range(8):

            images, labels = next(data_generator)
            predictions = model.predict(images)

            images = [image * 255 for image in images]
            images = [facecctv_ai.processing.scale_image(image, 100) for image in images]

            logger.info(vlogging.VisualRecord("image batch", images, str(predictions)))

def log_heatmaps(image_path_file, logger):

      model = facecctv_ai.models.get_vgg_model(facecctv_ai.config.image_shape)
      model.load_weights(facecctv_ai.config.model_path)

      paths = [path.strip() for path in facecctv_ai.utils.get_file_lines(image_path_file)]
      random.shuffle(paths)

      for path in tqdm.tqdm(paths[:10]):

            image = facecctv_ai.utils.get_image(path)

            

            heatmap = facecctv_ai.detections.Heatmap(image, model, facecctv_ai.config.face_search_config).get_heatmap()

            scaled_images = [255 * image, 255 * heatmap]
            scaled_images = [facecctv_ai.processing.scale_image(image, 200) for image in scaled_images]

            logger.info(vlogging.VisualRecord("image heatmap", scaled_images, str(image.shape)))

def log_face_detections(image_path_file, logger):

      model = facecctv_ai.models.get_vgg_model(facecctv_ai.config.image_shape)
      model.load_weights(facecctv_ai.config.model_path)

      paths = [path.strip() for path in facecctv_ai.utils.get_file_lines(image_path_file)]
      random.shuffle(paths)

      for path in tqdm.tqdm(paths[:10]):

            image = facecctv_ai.utils.get_image(path)

            detections = facecctv_ai.detections.FaceDetection(image, model, facecctv_ai.config.face_search_config).get_face_detection()

            for face_detection in detections:
                  facecctv_ai.geometry.draw_bounding_box(image, face_detection.bounding_box, color=(0, 255, 0), thickness=3)

            logger.info(vlogging.VisualRecord("image detections", image * 255, "{} - {}".format(path, str(image.shape))))

def main():

      logger = facecctv_ai.utils.get_logger(facecctv_ai.config.get_log_path)

      #dataset = "custom_dataset"
      dataset = "wider_face_dataset"

      dataset_path = os.path.join(facecctv_ai.config.dataset_path, dataset)

      image_path_file = facecctv_ai.utils.join(dataset_path, "training_images.txt")
      bounding_box_file = facecctv_ai.utils.join(dataset_path, "training_bounding_boxes.txt")

      generator = facecctv_ai.data_generator.get_data_generator(image_path_file, bounding_box_file, batch_size=8, crop_size=facecctv_ai.config.crop_size)

      log_face_detections(image_path_file, logger)

if __name__ == "__main__":
      main()