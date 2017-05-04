
import click

from functools import update_wrapper


def bmo_context(f):
    # Unpacks the context and send the actor and command.
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        return ctx.invoke(f, ctx.obj['actor'], ctx.obj['cmd'], *args, **kwargs)
    return update_wrapper(new_func, f)
