import plotly.figure_factory as ff

df = [
    dict(Task="System Evaluation", Start='2022-11-01', Finish='2022-12-31', Resource='Completed'),

    dict(Task="Hardware assessment", Start='2023-01-02', Finish='2023-01-06', Resource='Completed'),
    dict(Task="Image centering to FOV", Start='2023-01-03', Finish='2023-01-04', Resource='Completed'),

    dict(Task="Board recording with MSC", Start='2023-01-09', Finish='2023-03-13', Resource='Completed'),
    dict(Task="TMB tester for border detection", Start='2023-01-09', Finish='2023-01-13', Resource='Completed'),
    dict(Task="Seams algorithm inside boundaries", Start='2023-01-09', Finish='2023-01-13', Resource='Completed'),

    dict(Task="Dataset organization", Start='2022-12-10', Finish='2023-01-27', Resource='Completed'),
    dict(Task="Classifier model", Start='2023-01-16', Finish='2023-01-27', Resource='Failed'),
    dict(Task="Object Detector model for Seams", Start='2023-01-16', Finish='2023-02-01', Resource='Completed'),
    dict(Task="Add Holes and Souflure to model", Start='2023-01-16', Finish='2023-02-01', Resource='Completed'),
    dict(Task="Continuous model improvement", Start='2023-06-30', Finish='2023-09-13', Resource='Incomplete'),

    dict(Task="MSC integrated model", Start='2023-01-26', Finish='2023-04-10', Resource='Failed'),
    dict(Task="MSC Test & Debug", Start='2023-04-10', Finish='2023-05-30', Resource='Completed'),
    dict(Task="H-engine development", Start='2023-06-01', Finish='2023-06-30', Resource='Completed'),
    dict(Task="H-engine for Statistics", Start='2023-06-01', Finish='2023-07-31', Resource='Completed'),
    dict(Task="H-engine for Production", Start='2023-06-30', Finish='2023-07-31', Resource='Completed'),
    dict(Task="Outsourcing annotations", Start='2023-03-31', Finish='2023-09-13', Resource='In progress')

]

colors = {'Incomplete': 'rgb(253, 127, 63)',
          'Not Started': 'rgb(248, 183, 50)',
          'Completed': 'rgb(38, 222, 128)',
          'Failed': 'rgb(245, 3, 2',
          'In progress': 'rgb(68, 171, 241)'}

fig = ff.create_gantt(df, colors=colors,
                      index_col='Resource',
                      show_colorbar=True,
                      group_tasks=True)
fig.show()