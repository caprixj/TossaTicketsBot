def get_routers():
    from command.routed.handlers.public_handlers import router as public_handler_router
    from command.routed.handlers.creator_handlers import router as creator_handler_router
    from command.routed.callbacks.public_callbacks import router as public_callback_router

    return [
        public_handler_router,
        creator_handler_router,
        public_callback_router
    ]
