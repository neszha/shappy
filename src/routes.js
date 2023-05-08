import { Router } from 'express'
import controllers from './controllers.js'

const route = Router()

/** APIS */
route.get('/api/device/state', controllers.getDeviceState)
route.put('/api/device/state', controllers.updateDeviceState)
route.get('/api/device/activity', controllers.getActivity)
route.post('/api/device/activity', controllers.postActivity)
route.delete('/api/device/activity/:key', controllers.deleteActivity)

export default route