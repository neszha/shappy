import { Router } from 'express'
import controllers from './controllers.js'

const route = Router()

/** APIS */
route.get('/api/device/state', controllers.getDeviceState)
route.put('/api/device/state', controllers.updateDeviceState)

export default route