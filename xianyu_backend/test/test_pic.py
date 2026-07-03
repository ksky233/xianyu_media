from app.workflow.video_recongnizer_v2 import VideoRecongnizerV2
recongnizer = VideoRecongnizerV2(workflow_type=None)
graph_code = recongnizer.get_graph()
print(graph_code)
