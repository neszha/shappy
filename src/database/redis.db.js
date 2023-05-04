import dotenv from 'dotenv'
import process from 'process'
import { createClient } from 'redis'
import events from '../utils/events.js'

/** Membuat koneksi ke server Redis. */
dotenv.config()
const connection = process.env.REDIS_CONNECTION
const redis = createClient({ url: connection })

redis.connect().then(() => {
    events.emit('redis-connected')
    console.log('Terkoneksi ke server RedisDB.')
}).catch((err) => {
    console.log(err)
    process.exit()
})

export default redis
