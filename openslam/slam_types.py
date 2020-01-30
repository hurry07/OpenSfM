from opensfm import types
from opensfm import feature_loader
from opensfm import io
import slam_utils

class Frame(object):
    """Every image form the input is a Frame.
    Only selected frames become keyframes
    """
    def __init__(self, name, id, data):
        self.im_name = name
        self.image = io.imread(data._image_file(name), grayscale=True)  # The gray-scale image
        self.frame_id = id
        self.kf_id = -1  # if non-KF, id of "parent" KF
        self.world_pose = types.Pose()
        self.rel_pose_to_kf = types.Pose()

        self.img_pyr = [self.image]

        self.has_features = False
        self.descriptors = None
        self.points = None
        self.colors = None

        self.undist_pts = None
        self.keypts_in_cell = None

    def load_points_desc_colors(self):
        if self.has_features:
            return (self.points, self.descriptors, self.colors)
        return None

    def prepare_for_storage(self):
        """Called before storing frame in the mapper.
        Cleans up memory by releasing image, desc, points, colors
        """
        self.has_features = False
        self.descriptors, self.points, self.colors = None, None, None
        self.image = None

    def extract_features(self, data, do_extract=False):
        """Loads or extracts descriptors, points and colors"""
        if do_extract:
            self.points, self.descriptors, self.colors =\
                slam_utils.extract_features(self.im_name, data)
        else:
            self.points, self.descriptors, self.colors = \
                feature_loader.instance.load_points_features_colors(
                    data, self.im_name, masked=True)

        self.has_features = self.points is not None\
            and self.descriptors is not None\
            and self.colors is not None


class Keyframe(Frame):
    def __init__(self, frame: Frame, data, kf_id):
        """Initialize a new keyframe with a frame and a kf_id
        pdc is points, descriptors and colors as "triple"
        """
        # print("Creating KF: ", kf_id, len(self.landmarks_), frame.im_name)
        print("Creating KF: ", kf_id, frame.im_name)

        self.kf_id = kf_id  # unique_id
        self.im_name = frame.im_name
        self.frame_id = frame.frame_id
        self.kf_id = -1  # if non-KF, id of "parent" KF
        self.world_pose = frame.world_pose
        self.rel_pose_to_kf = types.Pose()  # since this is a keyframe, rel = I

        self.image = frame.image  # The gray-scale image
        self.has_features = frame.has_features
        self.points, self.descriptors, self.colors =\
            frame.load_points_desc_colors()




        # TODO: Think about this part. It is probably not needed since
        # we detect only features in first frame and then continue

        # check if features already exist in the frame
        # if pdc is not None:
        #     self.points, self.descriptors, self.colors = pdc
        # else:
        #     self.points, self.descriptors, self.colors = \
        #         feature_loader.instance.load_points_features_colors(
        #             data, self.im_name, masked=True)

    # def load_points_desc_colors(self):
    #     return (self.points, self.descriptors, self.colors)
