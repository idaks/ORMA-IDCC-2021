import argparse
from ORMA.orma import generate_dot, model_schema_evolution, translate_operator_json_to_graph, \
    generate_table_dot, split_recipe


def model_analysis():
    FUNCTION_MAP = {
        'parallel_view': generate_dot,
        'summary_view': model_schema_evolution,
        'table_view': generate_table_dot,
        'Clusters_Parallel_View': split_recipe
    }

    parser = argparse.ArgumentParser(description='OpenRefine Model Analysis')
    # parser.add_argument('command', choices=FUNCTION_MAP.keys() )
    parser.add_argument(
        "--project_id",
        type=int,
        default=2124203262743,
        help='Input Project ID'
    )
    parser.add_argument(
        "--output",
        type=str,
        default='usecase1/orma_exp.gv',
        help='path of the output gv file'
    )
    parser.add_argument(
        'command', choices=FUNCTION_MAP.keys()
    )

    args = parser.parse_args()
    func = FUNCTION_MAP[args.command]

    func(args.project_id, args.output)


if __name__ == '__main__':
    model_analysis()
    # history_update()
