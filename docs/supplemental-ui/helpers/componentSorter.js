'use strict'

module.exports = (components, sortOrder = undefined) => {
  if (sortOrder) {
    const sort = sortOrder.split(',').map((componentName) => componentName.trim())
    return sort.reduce((accum, name) => {
      if (components[name]) {
        accum.push(components[name])
      } else {
        console.log(`no such component to sort: ${name}`)
      }
      return accum
    }, [])
  } else {
    return components
  }
}
