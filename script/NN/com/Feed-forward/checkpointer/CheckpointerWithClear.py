import neat
import os, glob

class CheckpointerWithClear(neat.Checkpointer):

  def __init__(self, 
                generation_interval=100, 
                time_interval_seconds=300, 
                filename_prefix='neat-checkpoint-'):
    super(CheckpointerWithClear, self).__init__(generation_interval, time_interval_seconds, filename_prefix)
  
  def save_checkpoint(self, config, population, species_set, generation):
    super(CheckpointerWithClear, self).save_checkpoint(config, population, species_set, generation)
    self.clear_checkpoints()

  def clear_checkpoints(self):
      checkpoint_file_list = glob.glob(os.path.join(os.curdir, self.filename_prefix + "*"))
      if len(checkpoint_file_list) > 1:
        last_checkpoint = max(checkpoint_file_list, key=lambda file: os.path.getmtime(file))
        try:
          for filename in checkpoint_file_list:
            if not filename.endswith(last_checkpoint):
              os.remove(os.path.join(os.curdir, filename))
        except:
          print("Error while deleting file : ", filename)

      bk_file_list = glob.glob(os.path.join(os.curdir, "*.bk2"))
      if len(bk_file_list) > 0:
        last_bk = max(bk_file_list, key=lambda file: os.path.getmtime(file))
        try:
           for filename in bk_file_list:
                if not filename.endswith(last_bk):
                    file_path = os.path.join(os.curdir, filename)
                    os.remove(file_path)
        except:
          print("Error while deleting file : ", file_path)


