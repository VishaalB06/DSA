try:
    import web_map
    print('HAS_BUILD_MAP_HTML=', hasattr(web_map, 'build_map_html'))
    print('HAS_BUILD_ROUTE_MAP_HTML=', hasattr(web_map, 'build_route_map_html'))
except Exception as e:
    import traceback
    traceback.print_exc()
    print('IMPORT ERROR:', type(e).__name__, e)
