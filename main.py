import argparse
from ORMA.orma import model_schema_evolution, \
    generate_table_dot, split_recipe, parallel_view_main


def model_analysis():
    FUNCTION_MAP = {
        'parallel_view': parallel_view_main,
        'schema_view': model_schema_evolution,
        'table_view': generate_table_dot,
        'modular_views': split_recipe
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
        default='usecase1/table_view/',
        help='path of the output gv file'
    )
    parser.add_argument(
        'command', choices=FUNCTION_MAP.keys()
    )
    parser.add_argument(
        '--combined',
        type=bool,
        default=False,
        help='return the combined table view'
    )

    args = parser.parse_args()
    func = FUNCTION_MAP[args.command]
    if args.command == 'table_view':
        func(args.project_id, args.output, args.combined)
    else:
        func(args.project_id, args.output)


if __name__ == '__main__':
    model_analysis()
    # history_update()
