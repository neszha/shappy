import cors from 'cors'
import dotenv from 'dotenv'
import morgan from 'morgan'
import express from 'express'
import { createServer } from 'http'
import './database/index.js'
import routes from './routes.js'

const ROOT = process.cwd();

/** Create express app. */
dotenv.config()
const app = express()
const httpServer = createServer(app)

/** Middlewhare express in main level. */
app.use(cors())
app.use(morgan('tiny'))
app.use('/', express.static(`${ROOT}/client`));

/** Setup routes middlewhare express. */
app.use('/', routes)

/** Starting HTTP server. */
const port = process.env.PORT || 8000
httpServer.listen(port, () => {
    console.clear()
    console.log(`Server berjalan di 0.0.0.0:${port}`)
    console.log('.\n.\n.')
})
