import plotly.figure_factory as ff

df = [

      dict(Task="System Evaluation", Start='2022-11-01', Finish='2022-12-31', Resource='Complete'),

      dict(Task="Hardware assessment", Start='2023-01-02', Finish='2023-01-06', Resource='Complete'),
      dict(Task="Image centering to FOV", Start='2023-01-03', Finish='2023-01-04', Resource='Complete'),

      dict(Task="Board recording with MSC", Start='2023-01-09', Finish='2023-01-13', Resource='Complete'),
      dict(Task="TMB tester for border detection", Start='2023-01-09', Finish='2023-01-13', Resource='Complete'),
      dict(Task="Seams algorithm inside boundaries", Start='2023-01-09', Finish='2023-01-13', Resource='Complete'),

      dict(Task="Dataset organization", Start='2022-12-10', Finish='2023-01-27', Resource='Complete'),
      dict(Task="Model Training: Classifier", Start='2023-01-16', Finish='2023-01-27', Resource='Complete'),
      dict(Task="Model Training: Object Detector", Start='2023-01-16', Finish='2023-02-01', Resource='Complete'),
      dict(Task="Model Training: Add holes", Start='2023-01-16', Finish='2023-02-01', Resource='Complete'),

      dict(Task="Model Integration: MSC development", Start='2023-01-26', Finish='2023-04-10', Resource='Incomplete'),
      dict(Task="Test & Debug", Start='2023-04-10', Finish='2023-09-30', Resource='Incomplete'),
      dict(Task="Outsourcing annotations", Start='2023-03-31', Finish='2023-09-30', Resource='Not Started')
]

colors = {'Incomplete': 'rgb(68, 171, 241)',
          'Not Started': 'rgb(248, 183, 50)',
          'Complete': 'rgb(38, 222, 128)'}

fig = ff.create_gantt(df, colors=colors,
                      index_col='Resource',
                      show_colorbar=True,
                      group_tasks=True)
fig.show()