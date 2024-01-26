import unittest
import json

from apollo_msgs import PerceptionObstacle


class ObstacleTransformerTest(unittest.TestCase):

    def setUp(self):
        with open(
                "./samples/test_data/00000009.00000_perception_obstacles.json",
                'r') as file:
            self.json_data = file.read()

    # def test_obstacle_transformer(self):

    #     raw_dict = json.loads(self.json_data)
    #     obstacle_with_header_list = raw_dict["PERCEPTION_OBSTACLES"]

    #     res = []
    #     for obstacle_with_header in obstacle_with_header_list:
    #         obstacles = obstacle_with_header["perception_obstacle"]

    #         for obstacle in obstacles:
    #             res.append(PerceptionObstacle(**obstacle))

    #     grouped_dict = {}
    #     for obstacle in res:
    #         if obstacle.id not in grouped_dict:
    #             grouped_dict[obstacle.id] = [obstacle]
    #         else:
    #             last_obstacle = grouped_dict[obstacle.id][-1]
    #             is_stand_still = obstacle.position.x == last_obstacle.position.x and obstacle.position.y == last_obstacle.position.y and obstacle.position.z == last_obstacle.position.z

    #             if not is_stand_still:
    #                 grouped_dict[obstacle.id].append(obstacle)

    #     for id, obs in grouped_dict.items():
    #         print(id, len(obs), obs[0].type)

    #     self.assertEqual(True, False)
