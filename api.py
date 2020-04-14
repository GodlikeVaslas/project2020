from flask import Flask
from flask_restful import reqparse, Api, Resource
from CLARA import clara

app = Flask(__name__)
api = Api(app)

experiments = {}


class Experiment(Resource):
    def get(self, exp_id):
        if exp_id not in experiments:
            return "Experiment does not exist", 404
        return experiments[exp_id]

    def post(self, exp_id):
        parser = reqparse.RequestParser()
        parser.add_argument('_runs', type=int)
        parser.add_argument('_data')
        parser.add_argument('_k', type=int)
        parser.add_argument('_fn')
        parser.add_argument('_niter', type=int)
        args = parser.parse_args()
        best_choices, best_results = clara(args['_runs'], args['_data'], args['_k'], args['_fn'], args['_niter'])
        result = [best_choices, best_results]
        return result, 201


class ExperimentList(Resource):
    def get(self):
        return experiments

    def post(self):
        if (len(experiments.keys()) == 0):
            exp_id = 1
        else:
            exp_id = int(max(experiments.keys())) + 1
        experiments[exp_id] = {}
        return experiments[exp_id], 201


api.add_resource(ExperimentList, '/experiments')
api.add_resource(Experiment, '/experiments/<int:exp_id>')

if __name__ == '__main__':
    app.run()