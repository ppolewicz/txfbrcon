#!/bin/bash
export PYTHONPATH=. # this is needed so modules can be imported from local directory
twistd -ny service.tac

