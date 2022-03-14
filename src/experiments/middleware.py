from .experiments import experiments


def experiments_middleware(get_response):
    def middleware(request):
        exps = {}

        for exp in experiments:
            exps[exp.slug] = exp(request)

        request.EXPERIMENTS = exps
        response = get_response(request)
        return response

    return middleware
