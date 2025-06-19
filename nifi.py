import nipyapi
from nipyapi import canvas, nifi
# Connect to your secure NiFi instance
nipyapi.config.nifi_config.host = 'https://localhost:8443/nifi-api'
nipyapi.security.service_login(service="nifi", username="admin", password="admin_password")




# Get your target process group by ID
pg = canvas.get_process_group('5fb81e8e-0197-1000-f4a4-b21e0342cb14')

# Utility to add a processor
def add_processor(pg, proc_type, name, position, props):
    return canvas.create_processor(
        parent_pg=pg,
        processor=nifi.ProcessorDTO(
            type=proc_type,
            name=name
        ),
        location=position
    ).component

# Create processors with minimal config

coords = [(0,0), (200,0), (400,0), (600,0), (800,0), (1000,0)]
processors = []
processors.append(add_processor(pg, 'org.apache.nifi.processors.standard.GetFile', 'GetFile', coords[0], {
    'Input Directory': '/Users/nimalesh/Downloads/HDFS_v1',
    'File Filter': 'HDFS.txt',
    'Keep Source File': 'false'
}))
processors.append(add_processor(pg, 'org.apache.nifi.processors.standard.SplitFile', 'SplitFile', coords[1], {
    'Split Size': '10 MB'
}))
for i, lines in enumerate([100000, 1000, 100, 1]):
    processors.append(add_processor(pg,
        'org.apache.nifi.processors.standard.SplitText',
        f'SplitText{lines}',
        coords[2 + i],
        {'Line Split Count': str(lines), 'Remove Trailing Newlines': 'true'}
    ))
processors.append(add_processor(pg,
    'org.apache.nifi.processors.kafka.pubsub.PublishKafka_2_6',
    'PublishKafka',
    coords[-1],
    {
      'bootstrap.servers': 'localhost:9092',
      'topic': 'nasa_log',
      'acks': 'all',
      'use-transactions': 'true'
    }
))

# Chain the processors
for src, dst in zip(processors, processors[1:]):
    canvas.create_connection(src, dst, ['success' if 'GetFile' in src.name else 'splits'])

# Start all processors
for proc in processors:
    canvas.schedule_processor(proc, True)
