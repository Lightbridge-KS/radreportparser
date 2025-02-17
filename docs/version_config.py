from importlib_metadata import version as _version

v = f"""VERSION={_version('radreportparser')}"""

f = open("_environment", "w")
f.write(v)