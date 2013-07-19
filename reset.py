#! /usr/bin/env python

import model

model.paladar_db.connect()

model.create_tables()

model.ChannelType.create(name='regular')
model.ChannelType.create(name='feedzilla')

model.User.create(
  handle = 'marcel',
  name = 'Marcel Rodrigues',
  email = 'marcel@rodrigues.com',
  language = 'pt-BR',
  hashed_password = '$p5k2$1000$hpNXFLbvtsA1ChjvD4mjyw==$CHcBuus22FsoH6CtWJ4ZNtGvgiM='
)

model.User.create(
  handle = 'demo',
  name = 'Demonstration User',
  email = 'demo@user.com',
  hashed_password = '$p5k2$1000$pVD2w23HrzLPAH8jlvF5oA==$0-zXAwRTXgihVp0s_QqbndWrEOM='
)

model.paladar_db.close()
