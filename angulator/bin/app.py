import web
import os
import slitoptimiser
import utils

urls = (
  '/', 'index',
  '/static/images/(.*)', 'images' #this is where the image folder is located....
)

app = web.application(urls, globals())

render = web.template.render('templates/')

class index:
    def GET(self):
        d = {'L12': 2859.5,
            'L2S': 276,
            'resolution' : 0.05,
             'footprint' : 50,
             'lambdamin' : 2.8,
             'lambdamax' : 18.5,
             'a1' : 0.5,
             'a2' : 2,
             'a3' : 6,
             }
        calculate_variables(d)
        return render.angulator(d)
        
    def POST(self):
        form = web.input()
        calculate_variables(form)
        return render.angulator(form)

class images:
    def GET(self, name):
        ext = name.split(".")[-1] # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"}

        if name in os.listdir('/static/images'):  # Security
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('images/%s'%name,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()
            
def calculate_variables(d):
    minqvals = []
    maxqvals = []
    minqvals.append(utils.qcalc(float(d['a1']), float(d['lambdamax'])))
    minqvals.append(utils.qcalc(float(d['a2']), float(d['lambdamax'])))
    minqvals.append(utils.qcalc(float(d['a3']), float(d['lambdamax'])))
    maxqvals.append(utils.qcalc(float(d['a1']), float(d['lambdamin'])))
    maxqvals.append(utils.qcalc(float(d['a2']), float(d['lambdamin'])))
    maxqvals.append(utils.qcalc(float(d['a3']), float(d['lambdamin'])))
    d['minqvals'] = minqvals
    d['maxqvals'] = maxqvals
    d1, d2 = slitoptimiser.slitoptimiser(float(d['footprint']),
                             float(d['resolution']),
                              L12 = float(d['L12']),
                                L2S = float(d['L2S']),
                                 verbose = False)
    d['slit1'] = [d1 * float(d['a1']), d1 * float(d['a2']), d1 * float(d['a3'])]
    d['slit2'] = [d2 * float(d['a1']), d2 * float(d['a2']), d2 * float(d['a3'])]
    
if __name__ == "__main__":
    app.run()
